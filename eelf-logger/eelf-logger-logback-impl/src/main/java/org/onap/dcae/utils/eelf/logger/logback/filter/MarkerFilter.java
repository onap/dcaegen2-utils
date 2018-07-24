/*
 * ================================================================================
 * Copyright (c) 2017 AT&T Intellectual Property. All rights reserved.
 * ================================================================================
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 * ============LICENSE_END=========================================================
 *
 * ECOMP is a trademark and service mark of AT&T Intellectual Property.
 */

package org.onap.dcae.utils.eelf.logger.logback.filter;

import ch.qos.logback.classic.spi.ILoggingEvent;
import ch.qos.logback.core.filter.AbstractMatcherFilter;
import ch.qos.logback.core.spi.FilterReply;
import org.slf4j.Marker;
import org.slf4j.MarkerFactory;

import java.util.HashSet;
import java.util.Set;

/**
 * Logback Marker filter
 *
 * @author Rajiv Singla
 */
public class MarkerFilter extends AbstractMatcherFilter<ILoggingEvent> {

    private String markersString;
    private Set<Marker> markersToAccept = new HashSet<>();

    @Override
    public FilterReply decide(final ILoggingEvent event) {

        if (!isStarted()) {
            return FilterReply.NEUTRAL;
        }

        if (markersToAccept.contains(event.getMarker())) {
            return onMatch;
        } else {
            return onMismatch;
        }
    }

    public void setMarkers(String markersString) {
        this.markersString = markersString;
    }


    public void start() {

        if (markersString != null && markersString.trim().split(",").length > 0) {

            final String[] markerStrings = markersString.trim().split(",");
            for (String markerString : markerStrings) {
                markersToAccept.add(MarkerFactory.getMarker(markerString.trim()));
            }
            super.start();
        }
    }
}
